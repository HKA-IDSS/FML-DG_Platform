import { Strategy, MLModel, Dataset } from 'api/models';

export type ArtifactType = 'strategy' | 'model' | 'dataset';
export type Artifact =
    | {
          artifactType: 'strategy';
          value: Strategy;
      }
    | {
          artifactType: 'model';
          value: MLModel;
      }
    | {
          artifactType: 'dataset';
          value: Dataset;
      };

export type ComparisonRow = {
    key: string;
    attribute: string;
    a: React.ReactNode;
    b: React.ReactNode;
    type: 'primitive' | 'object' | 'array';
    valueA?: any;
    valueB?: any;
    childrenData?: ComparisonRow[];
};
