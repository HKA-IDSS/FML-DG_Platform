import React from 'react';
import { Metric } from '../../api/models';
import { useMultipleTestEvaluations, useMultipleTestShapleyValues } from '../../hooks/evaluation';
import { parseCsvResponse } from './ExtractCsv';
import { Divider, Flex, Spin } from 'antd';
import { Bar, Column, Line } from '@ant-design/plots';

interface ResultsChartProps {
    evaluationData?: Record<Metric['type'], string>;
    shapleyData?: Record<Metric['type'], string>;
    evaluationMetrics: Metric['type'][];
    shapleyMetrics: Metric['type'][];
}

type LinePlotDataPoint = {
    round: number;
    value: number;
    client: string;
};

type BarPlotDataPoint = {
    value: number;
    client: string;
    evaluator: string;
};

const ResultsChart = ({
                          evaluationData,
                          shapleyData,
                          evaluationMetrics,
                          shapleyMetrics,
                      }: ResultsChartProps) => {
    return (
        <Flex className="mb-4 flex-col">
            {/* Evaluation */}
            {evaluationMetrics.length === 0 &&(
                <div>No Evaluation Metrics</div>
            )}

            {evaluationMetrics.map(metric => (
                <LineMetricChart
                    metric={metric}
                    data={evaluationData?.[metric]}
                />
            ))}

            {/* Shapley */}
            {shapleyMetrics.length > 0 && <Divider>Shapley Values</Divider>}

            {shapleyMetrics.length === 0 && (
                <div>No Shapley Values</div>
            )}

            {shapleyMetrics.map(metric => (
                <BarMetricChart
                    metric={metric}
                    data={shapleyData?.[metric]}
                />
            ))}
        </Flex>
    );
};


export default ResultsChart;

const metricRanges: Record<string, { domainMin: number; domainMax: number }> = {
    accuracy: { domainMin: 0, domainMax: 1 },
    crossentropy: { domainMin: 0, domainMax: 3 },
    f1score: { domainMin: 0, domainMax: 1 },
    mcc: { domainMin: -1, domainMax: 1 },
    cosinesimilarity: { domainMin: -1, domainMax: 1 },
};

type MetricChartProps = {
    metric: Metric['type'],
    data?: string
};

const LineMetricChart = ({ metric, data }: MetricChartProps) => {
    const processData: LinePlotDataPoint[] = React.useMemo(() => {
        if (!data) return [];
        let res = parseCsvResponse(data, metric, false);
        const dataPoints: LinePlotDataPoint[] = [];
        res.forEach((c) => {
            const metricObj = c.metrics[0];
            const values = metricObj.values;
            // @ts-ignore
            const rounds = c.rounds;
            for (let i = 0; i < rounds.length; i++) {
                dataPoints.push({
                    round: rounds[i],
                    value: values[i],
                    client: c.client,
                });
            }
        });
        return dataPoints;
    }, [data, metric]);

    const yDomain = metricRanges[metric] || { domainMin: 0, domainMax: 1 };

    return (
        <>
            <Divider orientation="left">{metric}</Divider>
            <Line
                data={processData}
                xField="round"
                yField="value"
                colorField="client"
                interaction={{ tooltip: { marker: false } }}
                scale={{ y: yDomain }}
                style={{ lineWidth: 2 }}
            />
        </>
    );
};

const BarMetricChart = ({metric, data}: MetricChartProps) => {
    const processData: BarPlotDataPoint[] = React.useMemo(() => {
        if (!data) return [];
        let res = parseCsvResponse(data, metric, true);
        const dataPoints: BarPlotDataPoint[] = [];
        res.forEach((c) => {
            const metricObj = c.metrics[0];
            const values = metricObj.values;
            // @ts-ignore
            const evaluators = c.evaluator;
            for (let i = 0; i < evaluators.length; i++) {
                dataPoints.push({
                    evaluator: evaluators[i],
                    value: values[i],
                    client: c.client,
                });
            }
        });
        return dataPoints;
    }, [data, metric]);

    const yDomain = metricRanges[metric] || { domainMin: 0, domainMax: 1 };

    return (
        <>
            <Divider orientation="left">{metric}</Divider>
            <Column
                data={processData}
                xField="evaluator"
                yField="value"
                colorField="client"
                group={true}
                interaction={{ tooltip: { marker: false } }}
                scale={{ y: yDomain }}
                style={{ lineWidth: 2 }}
            />
        </>
    );
};
