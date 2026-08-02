#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function installSkills() {
  const cwd = process.cwd();
  
  // Detect target skill directory in user project
  const possibleTargets = [
    path.join(cwd, '.agents', 'skills'),
    path.join(cwd, '.gemini', 'skills'),
    path.join(cwd, '.cursor', 'skills'),
    path.join(cwd, '.claude', 'skills')
  ];

  let targetDir = possibleTargets.find(dir => fs.existsSync(path.dirname(dir))) || possibleTargets[0];
  const sourceSkillsDir = path.join(__dirname, '..', '.agents', 'skills');

  if (!fs.existsSync(sourceSkillsDir)) {
    console.error(`Error: Source skills directory not found at ${sourceSkillsDir}`);
    process.exit(1);
  }

  console.log(`Installing LookML Dashboard Skills into: ${targetDir}`);
  copyRecursiveSync(sourceSkillsDir, targetDir);
  console.log('✅ Successfully installed LookML Dashboard Skills!');
  console.log('   - lookml-dashboards (with 10 element visualization parameter references)');
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
