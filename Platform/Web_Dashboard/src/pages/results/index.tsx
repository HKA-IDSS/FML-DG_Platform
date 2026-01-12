import React, { useState } from 'react';
import { ResultForm } from './ResultsForm';
import { Card, Divider } from 'antd';
import { Metric } from '../../api/models';
import ResultsChart from './ResultCharts';
import ResultsChartContainer from './ResultChartContainer';

const ResultsPage = () => {
    const [configurationId, setConfigurationId] = useState<string | null>(null);

    return (
        <div>
            <h1 className="text-lg font-semibold">Results</h1>
            <Divider />

            <div className="flex flex-col p-4">
                <Card className="mb-4 justify-items-center self-end">
                    <ResultForm
                        onSubmit={(values) => {
                            // assuming your form returns configuration_id
                            setConfigurationId(values.configuration_id);
                        }}
                        onCancel={() => console.log('Cancelled')}
                    />
                </Card>

                {/* Render charts only when configurationId exists */}
                {/*{configurationId && (*/}
                {/*    <ResultsChart*/}
                {/*        configuration_id={configurationId}*/}
                {/*        evaluationMetrics={[*/}
                {/*            'CrossEntropyLoss',*/}
                {/*            'Accuracy',*/}
                {/*            'MCC',*/}
                {/*            'F1ScoreMacro',*/}
                {/*        ] as Metric['type'][]}*/}
                {/*        shapleyMetrics={[*/}
                {/*            'CrossEntropyLoss',*/}
                {/*            'Accuracy',*/}
                {/*            'MCC',*/}
                {/*            'F1ScoreMacro',*/}
                {/*        ] as Metric['type'][]}*/}
                {/*    />*/}
                {/*)}*/}
                {configurationId && (
                    <ResultsChartContainer configuration_id={configurationId} />
                )}
            </div>
        </div>
    );
};

export default ResultsPage;
