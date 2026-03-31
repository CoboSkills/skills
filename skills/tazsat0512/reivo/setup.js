const { execSync } = require('child_process');

async function main() {
  console.log('');
  console.log('Reivo — AI Agent Cost Optimizer');
  console.log('================================');
  console.log('');

  // Check for REIVO_API_KEY
  const apiKey = process.env.REIVO_API_KEY;
  if (!apiKey) {
    console.log('⚠  REIVO_API_KEY not set.');
    console.log('');
    console.log('To get started:');
    console.log('  1. Sign up at https://app.reivo.dev');
    console.log('  2. Generate an API key in Settings (format: rv_...)');
    console.log('  3. Set the environment variable:');
    console.log('     export REIVO_API_KEY="rv_your_key_here"');
    console.log('');
    console.log('Then re-run: npx clawhub@latest run reivo');
    process.exit(1);
  }

  // Mask the key for display
  const masked = apiKey.length > 8
    ? `${apiKey.slice(0, 3)}...${apiKey.slice(-4)}`
    : '***';

  console.log(`✓ API key configured (${masked})`);

  // Check curl availability
  try {
    execSync('which curl', { stdio: 'ignore' });
    console.log('✓ curl available');
  } catch {
    console.log('✗ curl not found — required for API calls');
    process.exit(1);
  }

  // Quick connectivity check
  try {
    const res = execSync(
      `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${apiKey}" https://app.reivo.dev/api/v1/overview?days=1`,
      { timeout: 10000, encoding: 'utf-8' },
    ).trim();
    if (res === '200') {
      console.log('✓ Connected to Reivo API');
    } else if (res === '401') {
      console.log('✗ Invalid API key — check your REIVO_API_KEY');
      process.exit(1);
    } else {
      console.log(`⚠  API returned ${res} — may be temporary`);
    }
  } catch {
    console.log('⚠  Could not reach Reivo API — check your connection');
  }

  console.log('');
  console.log('Setup complete! Available commands:');
  console.log('  "show costs"          — View spending overview');
  console.log('  "budget status"       — Check budget & loop status');
  console.log('  "set budget to $50"   — Set a spending limit');
  console.log('  "optimization tips"   — Get cost reduction suggestions');
  console.log('  "open dashboard"      — Open the web dashboard');
  console.log('');
}

main();
