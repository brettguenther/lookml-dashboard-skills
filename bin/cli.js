#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const args = process.argv.slice(2);

// Handle validation flag
if (args.includes('--validate') || args.includes('-v')) {
  const vIndex = args.indexOf('--validate') !== -1 ? args.indexOf('--validate') : args.indexOf('-v');
  const targetPaths = args.slice(vIndex + 1).filter(a => !a.startsWith('-'));
  const validatorScript = path.join(__dirname, '..', 'scripts', 'validate_dashboard.py');

  if (targetPaths.length === 0) {
    targetPaths.push(process.cwd());
  }

  const result = spawnSync('python3', [validatorScript, ...targetPaths], { stdio: 'inherit' });
  process.exit(result.status || 0);
}

// Handle help
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
LookML Dashboard Skills CLI

Usage:
  npx @brettguenther/lookml-dashboard-skills [options]

Commands & Options:
  --validate, -v <path>   Validate LookML dashboard YAML files for fatal rendering bugs
  --target, -t <dir>      Specify target directory to install skills
  --help, -h              Show this help message
`);
  process.exit(0);
}

function installSkills() {
  const cwd = process.cwd();
  
  let targetDir = null;
  const targetFlagIndex = args.indexOf('--target') !== -1 ? args.indexOf('--target') : args.indexOf('-t');
  if (targetFlagIndex !== -1 && args[targetFlagIndex + 1]) {
    targetDir = path.resolve(cwd, args[targetFlagIndex + 1]);
  } else {
    // Detect target skill directory in user project
    const possibleTargets = [
      path.join(cwd, '.agents', 'skills'),
      path.join(cwd, '.gemini', 'skills'),
      path.join(cwd, '.cursor', 'skills'),
      path.join(cwd, '.claude', 'skills')
    ];
    targetDir = possibleTargets.find(dir => fs.existsSync(path.dirname(dir))) || possibleTargets[0];
  }

  const sourceSkillsDir = path.join(__dirname, '..', 'skills');

  if (!fs.existsSync(sourceSkillsDir)) {
    console.error(`Error: Source skills directory not found at ${sourceSkillsDir}`);
    process.exit(1);
  }

  console.log(`Installing LookML Dashboard Skills into: ${targetDir}`);
  copyRecursiveSync(sourceSkillsDir, targetDir);
  console.log('✅ Successfully installed LookML Dashboard Skills!');
  console.log('   - lookml-dashboards (with element visualization parameter references & dynamic fields)');
}

function copyRecursiveSync(src, dest) {
  if (fs.statSync(src).isDirectory()) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach(child => copyRecursiveSync(path.join(src, child), path.join(dest, child)));
  } else {
    fs.copyFileSync(src, dest);
  }
}

installSkills();
