import { Metric } from '../../api/models';
import { useMultipleTestEvaluations, useMultipleTestShapleyValues, useResultsData } from '../../hooks/evaluation';
import { Alert, Divider, Spin } from 'antd';
import ResultsChart from './ResultCharts';

const ResultsChartContainer = ({ configuration_id }: { configuration_id: string }) => {
    const evaluationMetrics: Metric['type'][] = [
        'CrossEntropyLoss',
        'Accuracy',
        'MCC',
        'F1ScoreMacro',
    ];

    const shapleyMetrics: Metric['type'][] = [
        'CrossEntropyLoss',
        'Accuracy',
        'MCC',
        'F1ScoreMacro',
    ];

    const {
        loading,
        fatalError,
        evaluation,
        shapley,
    } = useResultsData(
        configuration_id,
        evaluationMetrics,
        shapleyMetrics
    );

    if (loading) return <Spin />;

    if (fatalError) {
        return (
            <Alert
                type="error"
                message="Error loading results"
                showIcon
            />
        );
    }

    if (!evaluation.exists && !shapley.exists) {
        return (
            <Alert
                type="info"
                message="No results available"
                showIcon
            />
        );
    }

    return (
        <>
            <ResultsChart
                evaluationData={evaluation.data}
                shapleyData={shapley.data}
                evaluationMetrics={
                    evaluation.exists ? evaluationMetrics : []
                }
                shapleyMetrics={
                    shapley.exists ? shapleyMetrics : []
                }
            />

            {!shapley.exists && (
                <>
                    <Divider />
                    <Alert
                        type="info"
                        message="No Shapley values available"
                        showIcon
                    />
                </>
            )}
        </>
    );
};



export default ResultsChartContainer;
