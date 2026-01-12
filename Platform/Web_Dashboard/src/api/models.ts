export interface MongoID {
    _id: string;
}

export interface MongoIDAndVersion extends MongoID {
    _governance_id: string;
    _version: number;
    _current: boolean;
    _deleted: boolean;
}

export enum Status {
    PROPOSED = 'PROPOSED',
    ACCEPTED = 'ACCEPTED',
    REJECTED = 'REJECTED',
    OBSOLETE = 'OBSOLETE',
}

export interface WithStatus {
    status: Status;
}

// User Models
export interface AddUser {
    name: string;
    organisation_id: string;
    description?: string;
    ip?: string;
}

export interface User extends AddUser, MongoIDAndVersion {}

// Group Models
export interface AddGroup {
    name: string;
    description?: string;
}

export interface Group extends AddGroup, MongoIDAndVersion {
    strategies: string[];
    members: string[];
}

// Organisation Models
export interface AddOrganisation {
    name: string;
}

export interface Organisation extends AddOrganisation, MongoIDAndVersion {
    users: string[];
}

// Strategy Models
export interface AddStrategy {
    name: string;
    description?: string;
    comments?: string[];
    belonging_group: string;
}

export interface Strategy extends AddStrategy, MongoIDAndVersion {
    quality_requirements: string[];
    quality_requirements_proposals: string[];
    configurations: string[];
    configuration_proposals: string[];
}

// Quality Requirements Models
export enum CorrectnessMethods {
    CrossEntropyLoss = 'CrossEntropyLoss',
    Accuracy = 'Accuracy',
    F1Score = 'F1Score',
    AUC = 'AUC',
}

export interface Correctness {
    quality_req_type: 'Correctness';
    metric: CorrectnessMethods;
    required_min_value: number;
    required_max_value: number;
}

export interface Bias {
    quality_req_type: 'Bias';
    vulnerable_feature: string;
    accepted_threshold: number;
}

export interface Interpretability {
    quality_req_type: 'Interpretability';
}

export interface Robustness {
    quality_req_type: 'Robustness';
}

export interface Efficient {
    quality_req_type: 'Efficient';
}

export interface Security {
    quality_req_type: 'Security';
}

export interface Privacy {
    quality_req_type: 'Privacy';
}

export type QualityRequirementType =
    | Correctness
    | Bias
    | Interpretability
    | Robustness
    | Efficient
    | Security
    | Privacy;

export interface AddQualityRequirement {
    quality_requirement: QualityRequirementType;
}

export interface QualityRequirement extends AddQualityRequirement, MongoID {
    name: string;
}

// Proposal Models
export enum ProposalType {
    CONFIGURATION = 'configuration',
    QUALITY_REQUIREMENT = 'quality_requirement',
    INFORMATION_UPDATE = 'information_update',
    POLICY = 'policy',
}

export interface AddProposal {
    name: string;
    proposer?: string;
    group: string;
    strategy_id: string;
    content_variant: ProposalType;
    operation_variant?: 'create' | 'update' | 'remove';
    referenced_content?: string;
    proposal_content: AddQualityRequirement | AddConfiguration;
    reasoning: string;
}

export interface Proposal extends AddProposal, MongoID, WithStatus {
    votes: (PriorityVote | DecisionVote)[];
}

export interface PriorityVote {
    member: string;
    priority: number;
}

export interface DecisionVote {
    member: string;
    decision: boolean;
}

// Dataset Models
export enum FeatureType {
    INTEGER = 'integer',
    LONG = 'long',
    FLOAT = 'float',
    DOUBLE = 'double',
    STRING = 'string',
    BOOLEAN = 'boolean',
}

export enum EncodingType {
    NONE = 'none',
    ONE_HOT_ENCODER = 'one_hot_encoder',
    LABEL_ENCODER = 'label_encoder',
    STANDARD_ENCODER = 'standard_encoder',
    MIN_MAX_ENCODER = 'min_max_encoder',
}

export interface Feature {
    name: string;
    type: FeatureType;
    valid_values: any[];
    order_in_dataset: number;
    preprocessing?: EncodingType;
    description?: string;
    group: boolean;
    sub_features: string[];
    comments: string[];
}

export interface AddDataset {
    name: string;
    strategy_governance_id: string;
    structured: boolean;
    features: Feature[];
    description?: string;
    comments?: string[];
}

export interface Dataset extends AddDataset, MongoIDAndVersion {
    // proposer?: string;
}

// ML Model Models
export enum AlgorithmType {
    MLP = 'mlp',
    XGBOOST = 'xgboost',
    CNN = 'cnn',
    LNN = 'lstm',
    CUSTOM = 'custom',
}

export enum TypeHP {
    INTEGER = 'integer',
    FLOAT = 'float',
    CATEGORICAL = 'categorical',
}

export interface Hyperparameter {
    name: string;
    type_of_hyperparameter: TypeHP;
    valid_values: any[];
}

export interface MLP {
    algorithm: 'mlp';
    hyperparameters: Hyperparameter[];
}

export interface XGBoost {
    algorithm: 'xgboost';
    hyperparameters: Hyperparameter[];
}

export interface Custom {
    algorithm: 'custom';
    hyperparameters: Hyperparameter[];
}

export type MLModelUnion = MLP | XGBoost | Custom;

export interface AddMLModel {
    /** Data required to add a new ML Model. */
    name: string;
    strategy_governance_id: string;
    model: MLModelUnion; // Discriminated union
    description?: string;
    comments: string[];
}

export interface MLModel extends AddMLModel, MongoIDAndVersion {
    // proposer?: string;
}

// Configuration Models
export interface AddConfiguration {
    ml_model_id: string;
    ml_model_version: number;
    dataset_id: string;
    dataset_version: number;
    number_of_rounds: number;
    number_of_ho_rounds: number;
}

export interface Configuration extends AddConfiguration, MongoID, WithStatus {
    strategy_linked?: string;
}

export interface AddTrainingConfigurationInformation {
    configurationId: string;
    modelType: string;
    datasetId: string;

    parameters: {
        epochs?: number;
        batchSize?: number;
        learningRate?: number;
        optimizerType?: string;
        [key: string]: any;
    };

    metrics: {
        trainLoss?: number;
        validationLoss?: number;
        accuracy?: number;
        [key: string]: number | undefined;
    };

    trainingStartTime: string;
    trainingEndTime: string;

    status: 'completed' | 'failed' | 'in_progress';
    errorMessage?: string;
}

// Metadata Models
export interface Responsible {
    id?: string;
    governance_id: string;
    version?: string;
    current?: string;
    name?: string;
    organisation_id?: string;
    description?: string;
    ip?: string;
}

export interface ActivityModel {
    responsible: Responsible;
    name: string;
    affected_objects: Record<string, string>;
    start_time: string;
    end_time: string;
}

export interface NumOfActionModel {
    responsible: Responsible;
    num_of_actions: number;
}

export interface GroupedActivityModel {
    responsible: Responsible;
    actions: ActivityModel[];
}

export interface EntityModel {
    governance_id: string;
    version: number;
    timestamp: string;
}

export interface AgentModel {
    governance_id: string;
    version: number;
    timestamp: string;
}

export interface Metric {
    type: 'Accuracy' | 'CrossEntropyLoss' | 'F1ScoreMacro' | 'F1ScoreMicro' | 'CosineSimilarity' | 'MCC';
    values: number[];
}

export interface ClientResult {
    client: string;
    metrics: Metric[];
    rounds: number[];
}

export interface SVResult {
    client: string;
    metrics: Metric[];
    evaluator: string[];
}

export interface Evaluation {
    strategy_id: string;
    data: ClientResult[];
}

export interface EvaluationResult {
    _id: string; // UUID
    _deleted: boolean;
    configuration_id: string; // UUID
    metric_used: string[];
    shapley_values: boolean;
}
