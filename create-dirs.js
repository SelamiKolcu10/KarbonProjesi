const fs = require('fs');
const path = require('path');

const baseDir = 'c:/Users/selam/Desktop/KarbonSalınımProjesi/frontend';
const dirs = [
  'src/components/layout',
  'src/components/ui', 
  'src/components/providers',
  'src/pages/dashboard',
  'src/pages/upload',
  'src/pages/emission',
  'src/pages/projection',
  'src/pages/strategy',
  'src/pages/reports',
  'src/pages/notifications',
  'src/pages/settings',
  'src/pages/auth',
  'src/lib'
];

dirs.forEach(d => {
  const fullPath = path.join(baseDir, d);
  fs.mkdirSync(fullPath, { recursive: true });
  console.log('Created:', fullPath);
});
