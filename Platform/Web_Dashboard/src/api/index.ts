import axios from 'axios';
import { keycloak } from '../keycloak'; // Needed for creating API
import {
    AddUser,
    User,
    AddGroup,
    Group,
    AddOrganisation,
    Organisation,
    AddStrategy,
    Strategy,
    AddQualityRequirement,
    QualityRequirement,
    Proposal,
    AddProposal,
    Dataset,
    AddDataset,
    MLModel,
    AddMLModel,
    Configuration,
    AddConfiguration,
    ActivityModel,
    NumOfActionModel,
    GroupedActivityModel,
    EntityModel,
    AgentModel,
    MLModelUnion,
    Metric,
    AddTrainingConfigurationInformation,
} from './models'; // Importing the generated models

export const axiosApi = axios.create({
    baseURL: 'http://localhost/api1/', // URL to backend here
});

// Helper to refresh token, login if needed, and return a fresh token
async function ensureFreshToken(): Promise<string> {
    try {
        await keycloak.updateToken(30);
        return keycloak.token!;
    } catch (err) {
        // Token refresh failed, force login
        await keycloak.login();
        // After login, token will be refreshed, so return it
        return keycloak.token!;
    }
}

// Axios request interceptor
axiosApi.interceptors.request.use(
    async (config) => {
        const token = await ensureFreshToken();
        (config.headers as any) = {
            ...config.headers,
            Authorization: `Bearer ${token}`,
        };
        return config;
    },
    (error) => Promise.reject(error),
);

// Groups
const getGroups = () => axiosApi.get<Group[]>('/groups');
const getGroupById = (groupId: string, version: number = -1) =>
    axiosApi.get<Group>(`/groups/${groupId}?version=${version}`);
const insertGroup = (payload: AddGroup) => axiosApi.post<Group>('/groups', payload);
const deleteGroup = (groupId: string) => axiosApi.delete(`/groups/${groupId}`);
const updateGroup = (groupId: string, payload: AddGroup) => axiosApi.put(`/groups/governance_id/${groupId}`, payload);
const getAllMembers = (groupId: string) => axiosApi.get<User[]>(`/groups/${groupId}/members`);
const addMember = (groupId: string, userId: string) => axiosApi.post(`/groups/${groupId}/add/${userId}`, {});

// Strategies
const getStrategies = (group_governance_id: string) =>
    axiosApi.get<Strategy[]>(`/strategies/groups/${group_governance_id}?group_id=${group_governance_id}`);
const getStrategy = (strategy_governance_id: string, version: number = -1) =>
    axiosApi.get<Strategy>(`/strategies/${strategy_governance_id}?version=${version}`);
const insertStrategy = (payload: AddStrategy) => axiosApi.post<Strategy>('/strategies', payload);
const deleteStrategies = (strategyId: string, group_governance_id: string) =>
    axiosApi.delete(`/strategies/${strategyId}?group_id=${group_governance_id}`);
const updateStrategy = (strategyId: string, payload: AddStrategy) =>
    axiosApi.put<Strategy>(`/strategies/${strategyId}`, payload);

// Organisations
const getOrganisations = () => axiosApi.get<Organisation[]>('/organisations');
const getOrganisationById = (organisationId: string) => axiosApi.get<Organisation>(`/organisations/${organisationId}`);
const insertOrganisation = (payload: AddOrganisation) => axiosApi.post<Organisation>('/organisations', payload);
const deleteOrganisation = (organisationId: string) => axiosApi.delete(`/organisations/${organisationId}`);

// Quality Requirements
const getAllQualityRequirements = (strategyId: string, version?: number) =>
    axiosApi.get<QualityRequirement[]>(`/strategies/${strategyId}/quality_requirements?version=${version ?? -1}`);
const insertQualityRequirement = (groupId: string, strategyId: string, payload: AddQualityRequirement) =>
    axiosApi.post<QualityRequirement>(`/groups/${groupId}/strategies/${strategyId}/quality_requirements`, payload);

// ML Models
const getMLModels = () => axiosApi.get<MLModel[]>('/ml-models/');
const getMLModelById = (id: string, version: number = -1) =>
    axiosApi.get<MLModel>(`/ml-models/${id}?version=${version}`);
const insertMLModels = (payload: AddMLModel) => axiosApi.post<MLModel>('/ml-models', payload);
const updateMLModels = (mlModelId: string, payload: AddMLModel) =>
    axiosApi.put<MLModel>(`/ml-models/${mlModelId}`, payload);
const deleteMLModel = (mlModelId: string) => axiosApi.delete(`/ml-models/${mlModelId}`);

// Datasets
const getDatasets = () => axiosApi.get<Dataset[]>('/datasets');
const getDatasetById = (datasetId: string, version: number = -1) =>
    axiosApi.get<Dataset>(`/datasets/${datasetId}?version=${version}`);
const insertDataset = (payload: AddDataset) => axiosApi.post<Dataset>('/datasets', payload);
const deleteDataset = (datasetId: string) => axiosApi.delete(`/datasets/${datasetId}`);
const updateDataset = (datasetId: string, payload: AddDataset) =>
    axiosApi.put<Dataset>(`/datasets/${datasetId}`, payload);

// Configurations
const getConfigurations = (strategyId: string, version?: number) =>
    axiosApi.get<Configuration[]>(`/strategies/${strategyId}/configurations?version=${version ?? -1}`);
const insertConfiguration = (strategyId: string, payload: AddConfiguration) =>
    axiosApi.post<Configuration>(`/strategies/${strategyId}/configurations`, payload);
const deleteConfiguration = (strategyId: string, configId: string) =>
    axiosApi.delete(`/strategies/${strategyId}/configurations/${configId}`);

// Users
const getUser = (userId: string) => axiosApi.get<User>(`/users/${userId}`); // This is only for admin
const getUserName = (userId: string) => axiosApi.get<Pick<User, 'name'>>(`/users/only_name/${userId}`);
const getAllUsers = () => axiosApi.get<User[]>(`/users`); // This is only for admin
const getLoggedUser = (userId: string) => axiosApi.get<User>(`/logged_user/${userId}`);
const createUser = (payload: AddUser) => axiosApi.post<User>('/users', payload); // This is only for admin
const deleteUser = (userId: string) => axiosApi.delete(`/users/${userId}`); // This is only for admin

// Proposals
const insertQualityRequirementProposal = (payload: AddProposal) =>
    axiosApi.post<Proposal>('/proposals/quality_requirements', payload);
const insertConfigurationProposal = (payload: AddProposal) =>
    axiosApi.post<Proposal>('/proposals/configurations', payload);
const addPriorityVote = (proposalId: string, payload: { member: string; priority: number }) =>
    axiosApi.post(`/proposals/${proposalId}/votes`, payload);
const addDecisionVote = (proposalId: string, payload: { member: string; decision: boolean }) =>
    axiosApi.post(`/proposals/${proposalId}/votes`, payload);
const countQualityRequirementVotes = (strategyId: string, proposalId: string) =>
    axiosApi.post(`/proposals/${strategyId}/count_votes_qr/${proposalId}`);
const countConfigurationVotes = (strategyId: string) =>
    axiosApi.post(`/proposals/${strategyId}/count_votes_configuration_proposals`);
const getProposals = () => axiosApi.get<Proposal[]>(`/proposals/`);
const getProposalsByStrategy = (strategyId: string) => axiosApi.get<Proposal[]>(`/proposals/strategies/${strategyId}`);
const deleteProposal = (id: string) => axiosApi.delete(`/proposals/${id}`);

// Default Models
const getDefaultMLPModel = () => axiosApi.get<MLModelUnion>('/ml-models/default_model/mlp');
const getDefaultXGBoostModel = () => axiosApi.get<MLModelUnion>('/ml-models/default_model/xgboost');
const getDefaultModel = (model: string) =>
    axiosApi.get<MLModelUnion>(`/ml-models/default_model/${model.toLowerCase()}`);

// Metadata
const getActions = () => axiosApi.get<ActivityModel[]>('/metadata/actions');
const getNumOfActions = () => axiosApi.get<NumOfActionModel[]>('/metadata/actions/num');
const getGroupedActions = () => axiosApi.get<GroupedActivityModel[]>('/metadata/actions/grouped_by_user');
const getEntities = () => axiosApi.get<EntityModel[]>('/metadata/entities');
const getAgents = () => axiosApi.get<AgentModel[]>('/metadata/agents');

// Results
const getResultFile = (configurationId: string, fileId: string) =>
    axiosApi.get(`/results/evaluation/${configurationId}?file_id=${fileId}`, { responseType: 'blob' });
const uploadResultFile = (configurationId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return axiosApi.post(`/results/evaluations/${configurationId}`, formData);
};
const getEvaluationTest = (metric: Metric['type']) => axiosApi.get(`/results/evaluation/test/${metric}`);
const getShapleyValueTest = (metric: Metric['type']) => axiosApi.get(`results/shapley_value/test/${metric}`);
const getTrainingInformation = (configurationId: string) =>
    axiosApi.get(`/results/training_information/${configurationId}`);
const getEvaluation = (configurationId: string, metricName: string) =>
    axiosApi.get(`/results/evaluation/${configurationId}?metric_name=${metricName}`);
const getEvaluationFromConfig = (configurationId: string) =>
    axiosApi.get(`/results/evaluation/from_configuration/${configurationId}`);
const getShapleyValueFromConfig = (configurationId: string) =>
    axiosApi.get(`/shapley_value/from_configuration/${configurationId}`);
const getShapleyValues = (configurationId: string, metricName: string) =>
    axiosApi.get(`/results/shapley_values/${configurationId}?metric_name=${metricName}`, { responseType: 'blob' });
const getModel = (configurationId: string, modelType: string = 'MLP') =>
    axiosApi.get(`/results/models/${configurationId}?model_type=${modelType}`, { responseType: 'blob' });
const uploadTrainedModel = (configurationId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return axiosApi.post(`/results/models/${configurationId}`, formData);
};
const uploadTrainingInformation = (payload: AddTrainingConfigurationInformation) =>
    axiosApi.post('/results/training_information', payload);

//  all API functions
const apis = {
    getGroups,
    getGroupById,
    insertGroup,
    deleteGroup,
    updateGroup,
    getAllMembers,
    addMember,
    getStrategy,
    getStrategies,
    insertStrategy,
    deleteStrategies,
    updateStrategy,
    getAllQualityRequirements,
    insertQualityRequirement,
    getMLModels,
    getMLModelById,
    insertMLModels,
    updateMLModels,
    deleteMLModel,
    getDatasets,
    getDatasetById,
    insertDataset,
    deleteDataset,
    updateDataset,
    getConfigurations,
    insertConfiguration,
    deleteConfiguration,
    getUser,
    getUserName,
    getAllUsers,
    getLoggedUser,
    createUser,
    deleteUser,
    insertQualityRequirementProposal,
    insertConfigurationProposal,
    addPriorityVote,
    addDecisionVote,
    countQualityRequirementVotes,
    countConfigurationVotes,
    getDefaultMLPModel,
    getDefaultXGBoostModel,
    getDefaultModel,
    getResultFile,
    uploadResultFile,
    getActions,
    getNumOfActions,
    getGroupedActions,
    getEntities,
    getAgents,
    getOrganisations,
    getOrganisationById,
    insertOrganisation,
    deleteOrganisation,
    getEvaluationTest,
    getShapleyValueTest,
    getTrainingInformation,
    getEvaluation,
    getEvaluationFromConfig,
    getShapleyValueFromConfig,
    getShapleyValues,
    getModel,
    uploadTrainedModel,
    uploadTrainingInformation,
    getProposals,
    getProposalsByStrategy,
    deleteProposal,
};

export default apis;
