'use strict'

const assert = require('assert')
const syncProjectStage = require('../scripts/sync_proposal_project_stage.js')

const config = {
  project: {stage_field: 'Review stage'},
  stage_by_status: {
    'needs-triage': 'Completeness / duplicate check',
    released: 'Release'
  }
}

assert.deepStrictEqual(
  syncProjectStage.parseProjectUrl('https://github.com/orgs/ERAgriculture/projects/2'),
  {ownerType: 'organization', owner: 'ERAgriculture', number: 2}
)
assert.strictEqual(syncProjectStage.stageForStatus(undefined, config), 'Proposal')
assert.strictEqual(syncProjectStage.stageForStatus('released', config), 'Release')
assert.throws(() => syncProjectStage.parseProjectUrl('https://example.org/project/2'))

async function testExistingItemUpdate() {
  const calls = []
  const github = {
    graphql: async (query, variables) => {
      calls.push({query, variables})
      if (query.includes('query ProposalProject(')) {
        return {
          organization: {
            projectV2: {
              id: 'PROJECT',
              fields: {
                nodes: [{
                  id: 'FIELD',
                  name: 'Review stage',
                  options: [
                    {id: 'PROPOSAL', name: 'Proposal'},
                    {id: 'RELEASE', name: 'Release'}
                  ]
                }]
              }
            }
          }
        }
      }
      assert(query.includes('mutation SetProposalReviewStage('))
      return {updateProjectV2ItemFieldValue: {projectV2Item: {id: 'ITEM'}}}
    }
  }

  await syncProjectStage({
    github,
    projectUrl: 'https://github.com/orgs/ERAgriculture/projects/2',
    itemId: 'ITEM',
    issueNodeId: 'ISSUE',
    statusLabel: 'released',
    config
  })

  assert.strictEqual(calls.length, 2)
  assert.deepStrictEqual(calls[1].variables, {
    projectId: 'PROJECT',
    itemId: 'ITEM',
    fieldId: 'FIELD',
    optionId: 'RELEASE'
  })
}

async function testMissingItemIsAdded() {
  const calls = []
  const github = {
    graphql: async (query, variables) => {
      calls.push({query, variables})
      if (query.includes('query ProposalProject(')) {
        return {
          organization: {
            projectV2: {
              id: 'PROJECT',
              fields: {
                nodes: [{
                  id: 'FIELD',
                  name: 'Review stage',
                  options: [{id: 'PROPOSAL', name: 'Proposal'}]
                }]
              }
            }
          }
        }
      }
      if (query.includes('query ProposalProjectItem(')) {
        return {node: {projectItems: {nodes: []}}}
      }
      if (query.includes('mutation AddProposalProjectItem(')) {
        return {addProjectV2ItemById: {item: {id: 'NEW_ITEM'}}}
      }
      assert(query.includes('mutation SetProposalReviewStage('))
      return {updateProjectV2ItemFieldValue: {projectV2Item: {id: 'NEW_ITEM'}}}
    }
  }

  await syncProjectStage({
    github,
    projectUrl: 'https://github.com/orgs/ERAgriculture/projects/2',
    issueNodeId: 'ISSUE',
    config
  })

  assert.strictEqual(calls.length, 4)
  assert.deepStrictEqual(calls[2].variables, {projectId: 'PROJECT', contentId: 'ISSUE'})
  assert.strictEqual(calls[3].variables.itemId, 'NEW_ITEM')
}

async function main() {
  await testExistingItemUpdate()
  await testMissingItemIsAdded()
}

main()
  .then(() => console.log('Proposal project stage sync tests passed.'))
  .catch(error => {
    console.error(error)
    process.exitCode = 1
  })
