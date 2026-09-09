'use strict'

function parseProjectUrl(projectUrl) {
  const match = projectUrl.match(/^https:\/\/github\.com\/(orgs|users)\/([^/]+)\/projects\/(\d+)$/)
  if (!match) throw new Error(`Invalid GitHub project URL: ${projectUrl}`)
  return {
    ownerType: match[1] === 'orgs' ? 'organization' : 'user',
    owner: match[2],
    number: Number(match[3])
  }
}

function stageForStatus(statusLabel, config) {
  return statusLabel ? config.stage_by_status[statusLabel] : 'Proposal'
}

async function syncProposalProjectStage({
  github,
  projectUrl,
  itemId,
  issueNodeId,
  statusLabel,
  config
}) {
  const project = parseProjectUrl(projectUrl)
  const stageName = stageForStatus(statusLabel, config)
  if (!stageName) throw new Error(`No project stage configured for status: ${statusLabel}`)

  const projectResponse = await github.graphql(
    `query ProposalProject($owner: String!, $number: Int!) {
      ${project.ownerType}(login: $owner) {
        projectV2(number: $number) {
          id
          fields(first: 100) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
      }
    }`,
    {owner: project.owner, number: project.number}
  )
  const projectData = projectResponse[project.ownerType].projectV2
  const stageField = projectData.fields.nodes.find(field => field.name === config.project.stage_field)
  if (!stageField) throw new Error(`Project field not found: ${config.project.stage_field}`)
  const stageOption = stageField.options.find(option => option.name === stageName)
  if (!stageOption) throw new Error(`Project stage option not found: ${stageName}`)

  let projectItemId = itemId
  if (!projectItemId) {
    const itemResponse = await github.graphql(
      `query ProposalProjectItem($issueNodeId: ID!) {
        node(id: $issueNodeId) {
          ... on Issue {
            projectItems(first: 100) {
              nodes { id project { id } }
            }
          }
        }
      }`,
      {issueNodeId}
    )
    const existingItem = itemResponse.node.projectItems.nodes.find(item => item.project.id === projectData.id)
    if (existingItem) {
      projectItemId = existingItem.id
    } else {
      const addResponse = await github.graphql(
        `mutation AddProposalProjectItem($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }`,
        {projectId: projectData.id, contentId: issueNodeId}
      )
      projectItemId = addResponse.addProjectV2ItemById.item.id
    }
  }

  await github.graphql(
    `mutation SetProposalReviewStage(
      $projectId: ID!,
      $itemId: ID!,
      $fieldId: ID!,
      $optionId: String!
    ) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: {singleSelectOptionId: $optionId}
      }) {
        projectV2Item { id }
      }
    }`,
    {
      projectId: projectData.id,
      itemId: projectItemId,
      fieldId: stageField.id,
      optionId: stageOption.id
    }
  )
}

module.exports = syncProposalProjectStage
module.exports.parseProjectUrl = parseProjectUrl
module.exports.stageForStatus = stageForStatus
