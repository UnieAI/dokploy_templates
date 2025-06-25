const fs = require('fs');

const filePath = './meta.json';
const raw = fs.readFileSync(filePath, 'utf-8');
const data = JSON.parse(raw);

data.forEach((item) => {
  const tags = new Set(item.tags);
  tags.add("app");
  tags.add("CPU");
  item.tags = Array.from(tags);
});

fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
console.log('Tags updated.');
