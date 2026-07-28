// main.bicep — subscription-scope entry point for `azd up`.
// Creates a resource group and deploys the AI-901 demo resources into it.
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the azd environment; used to derive resource names.')
param environmentName string

@minLength(1)
@description('Primary location for all resources. Must support the chosen models AND Azure AI Content Understanding (e.g. swedencentral, westus, australiaeast).')
param location string

@description('Object ID of the signed-in user, for keyless RBAC. azd sets this automatically.')
param principalId string = ''

@allowed(['User', 'ServicePrincipal'])
@description('Type of the principal receiving RBAC roles.')
param principalType string = 'User'

@description('Disable shared-key (local) auth on the Foundry account so only Entra ID credentials work. Every demo is keyless; set to false only if you need the preview key-auth Speech MCP tool.')
param disableLocalAuth bool = true

// ---- Model configuration (override in azd env if needed) ----
param chatModelName string = 'gpt-5.1'
param chatModelVersion string = '2025-11-13'
param chatCapacity int = 30
param imageModelName string = 'gpt-image-1'
param imageModelVersion string = '2025-04-15'
param embeddingModelName string = 'text-embedding-3-small'
param embeddingModelVersion string = '1'
param embeddingCapacity int = 30
// Realtime model for the OPTIONAL Voice Live demo (Module 4, Part C).
param realtimeModelName string = 'gpt-realtime'
param realtimeModelVersion string = '2025-08-28'
param realtimeCapacity int = 1

var tags = { 'azd-env-name': environmentName }
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'ai901-resources'
  scope: rg
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    principalId: principalId
    principalType: principalType
    disableLocalAuth: disableLocalAuth
    chatModelName: chatModelName
    chatModelVersion: chatModelVersion
    chatCapacity: chatCapacity
    imageModelName: imageModelName
    imageModelVersion: imageModelVersion
    embeddingModelName: embeddingModelName
    embeddingModelVersion: embeddingModelVersion
    embeddingCapacity: embeddingCapacity
    realtimeModelName: realtimeModelName
    realtimeModelVersion: realtimeModelVersion
    realtimeCapacity: realtimeCapacity
  }
}

// These outputs are surfaced by azd as environment variables to the postprovision hook.
output FOUNDRY_PROJECT_ENDPOINT string = resources.outputs.FOUNDRY_PROJECT_ENDPOINT
output CONTENT_UNDERSTANDING_ENDPOINT string = resources.outputs.CONTENT_UNDERSTANDING_ENDPOINT
output LANGUAGE_ENDPOINT string = resources.outputs.LANGUAGE_ENDPOINT
output SPEECH_RESOURCE_ID string = resources.outputs.SPEECH_RESOURCE_ID
output CHAT_DEPLOYMENT string = resources.outputs.CHAT_DEPLOYMENT
output MULTIMODAL_DEPLOYMENT string = resources.outputs.MULTIMODAL_DEPLOYMENT
output IMAGE_DEPLOYMENT string = resources.outputs.IMAGE_DEPLOYMENT
output EMBEDDING_DEPLOYMENT string = resources.outputs.EMBEDDING_DEPLOYMENT
output VOICE_LIVE_MODEL string = resources.outputs.VOICE_LIVE_MODEL
output SPEECH_REGION string = location
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
