/**
 * @skill       appian-inspectpkg
 * @version     1.0.0
 * @description Inspect an Appian package ZIP before deploying via the v2 Deployment Management API.
 *
 * @security-manifest
 *   env-accessed:       APPIAN_BASE_URL, APPIAN_API_KEY
 *   external-endpoints: POST ${APPIAN_BASE_URL}/inspections, GET ${APPIAN_BASE_URL}/inspections/{uuid}
 *   file-operations:    reads package ZIP from user-supplied path (upload only, no writes)
 *   no-shell-execution: true
 *   no-third-party-exfiltration: true
 */
import fs from 'node:fs';
import path from 'node:path';

function loadEnv(configPath) {
    try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        for (const [key, val] of Object.entries(config)) {
            if (!process.env[key]) process.env[key] = String(val);
        }
    } catch { /* rely on inherited env */ }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Inspect an Appian package ZIP before deploying.
 * https://docs.appian.com/suite/help/25.4/Inspect_Package_API.html
 */
async function inspectPackage(zipPath, custFilePath = null) {
    const baseUrl = process.env.APPIAN_BASE_URL?.replace(/\/$/, '');
    const apiKey  = process.env.APPIAN_API_KEY;

    if (!baseUrl) throw new Error('APPIAN_BASE_URL is not set');
    if (!apiKey)  throw new Error('APPIAN_API_KEY is not set');
    if (!fs.existsSync(zipPath)) throw new Error(`Package file not found: ${zipPath}`);

    const zipName      = path.basename(zipPath);
    const jsonPayload  = { packageFileName: zipName };
    if (custFilePath) {
        if (!fs.existsSync(custFilePath)) throw new Error(`Customization file not found: ${custFilePath}`);
        jsonPayload.customizationFileName = path.basename(custFilePath);
    }

    const formData = new FormData();
    formData.append('json', JSON.stringify(jsonPayload));
    formData.append(zipName,
        new Blob([fs.readFileSync(zipPath)], { type: 'application/zip' }),
        zipName
    );
    if (custFilePath) {
        const custName = path.basename(custFilePath);
        formData.append(custName,
            new Blob([fs.readFileSync(custFilePath)], { type: 'text/plain' }),
            custName
        );
    }

    // 1. Trigger inspection
    const triggerUrl = `${baseUrl}/inspections`;
    console.log(`POST ${triggerUrl}`);
    console.log(`Inspecting: ${zipPath} (${(fs.statSync(zipPath).size / 1024).toFixed(1)} KB)\n`);

    const triggerRes = await fetch(triggerUrl, {
        method: 'POST',
        headers: { 'appian-api-key': apiKey },
        body: formData,
    });

    if (!triggerRes.ok) {
        const text = await triggerRes.text().catch(() => '');
        throw new Error(`Inspection trigger failed [${triggerRes.status}]: ${text}`);
    }

    const triggerData    = await triggerRes.json();
    const inspectionUuid = triggerData.uuid;
    if (!inspectionUuid) throw new Error(`No uuid in response: ${JSON.stringify(triggerData)}`);
    console.log(`inspectionUuid: ${inspectionUuid}`);

    // 2. Poll for completion
    const pollUrl    = `${baseUrl}/inspections/${inspectionUuid}`;
    let data;
    let status       = '';
    let attempt      = 0;
    const maxAttempts = 24; // 2 minutes

    while (status !== 'COMPLETED' && status !== 'FAILED' && attempt < maxAttempts) {
        await sleep(5000);
        attempt++;
        const pollRes = await fetch(pollUrl, { headers: { 'appian-api-key': apiKey } });
        if (!pollRes.ok) { console.warn(`Poll ${attempt} failed [${pollRes.status}]`); continue; }
        data   = await pollRes.json();
        status = data.status ?? '';
        console.log(`[${attempt}/${maxAttempts}] status: ${status}`);
    }

    if (!data)              throw new Error('No inspection result received');
    if (status === 'FAILED') throw new Error(`Inspection system error: ${JSON.stringify(data)}`);

    // 3. Print results
    const summary  = data.summary ?? {};
    const expected = summary.objectsExpected ?? {};
    const problems = summary.problems ?? {};
    const errors   = problems.errors   ?? [];
    const warnings = problems.warnings ?? [];

    console.log(`\n=== Inspection Results ===`);
    console.log(`Objects expected — total: ${expected.total ?? '?'}, imported: ${expected.imported ?? '?'}, skipped: ${expected.skipped ?? '?'}, failed: ${expected.failed ?? '?'}`);

    if (errors.length > 0) {
        console.log(`\nErrors (${errors.length}):`);
        for (const e of errors) console.log(`  [${e.objectName ?? e.objectUuid ?? 'unknown'}] ${e.errorMessage}`);
    } else {
        console.log('\nNo errors.');
    }

    if (warnings.length > 0) {
        console.log(`\nWarnings (${warnings.length}):`);
        for (const w of warnings) console.log(`  [${w.objectName ?? w.objectUuid ?? 'unknown'}] ${w.warningMessage}`);
    } else {
        console.log('No warnings.');
    }

    return { inspectionUuid, status, expected, errors, warnings };
}

// CLI entry point
// Usage: node index.js <zipPath> [customizationFilePath]
const zipPath      = process.argv[2];
const custFilePath = process.argv[3] && process.argv[3] !== 'null' ? process.argv[3] : null;

if (!zipPath) {
    console.error('Usage: node index.js <zipPath> [customizationFilePath]');
    process.exit(1);
}

const envFile = path.join(process.cwd(), 'appian.json');
loadEnv(envFile);

inspectPackage(zipPath, custFilePath)
    .then(() => {})
    .catch(err => { console.error('\nError:', err.message); process.exit(1); });
