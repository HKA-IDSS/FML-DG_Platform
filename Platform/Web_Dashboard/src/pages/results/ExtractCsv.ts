import { ClientResult, Metric, SVResult } from '../../api/models';

/**
 * parses csv for clientResult
 * @param csvData
 * @param metricType
 * @param shapley
 */
export function parseCsvResponse(csvData: string, metricType: Metric["type"], shapley: boolean): ClientResult[] | SVResult[] {
    const lines = csvData.split('\n').map(value => value.trim());
    if (lines.length === 0) {
        throw new Error('Cannot parse empty CSV data');
    }
    const header = lines[0].split(',').map(value => value.trim());
    const clients: string[] = header.slice(1);
    let clientResults: ClientResult[] | SVResult[] = [];
    if (shapley) {
        for (let i = 0; i < clients.length; i++) {
            // @ts-ignore
            clientResults.push({
                client: clients[i],
                evaluator: [],
                metrics: [{
                    type: metricType,
                    values: [],
                }],
            });
        }
    } else {
        for (let i = 0; i < clients.length; i++) {
            // @ts-ignore
            clientResults.push({
                client: clients[i],
                rounds: [],
                metrics: [{
                    type: metricType,
                    values: [],
                }],
            });
        }
    }

    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim().length === 0) {
            continue;
        }
        const row = lines[i].split(',').map(value => value.trim());
        if (row.length !== header.length) {
            console.error(lines[i]);
            throw new Error('Invalid CSV data');
        }
        if (row.length !== clients.length + 1) {
            throw new Error('Invalid CSV data. Client mismatch');
        }

        if (shapley) {
            // @ts-ignore
            clientResults.forEach(cr => cr.evaluator.push(row[0]));
        } else {
            // @ts-ignore
            clientResults.forEach(cr => cr.rounds.push(i));
        }
        for (let j = 1; j < row.length; j++) {
            clientResults[j - 1].metrics[0].values.push(parseFloat(row[j]));
        }
    }
    return clientResults;
}



/**
 * merges several clientResults into one result, for future use
 * @param clientResults
 */
export function mergeClientResults(clientResults: ClientResult[]): ClientResult {
    return clientResults[0];
}
