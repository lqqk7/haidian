const H = require('path').resolve(__dirname, '../', 'w81-basemap/html') + "/";

const LU_ZH_NOTE = '图面旋转 90° · 北向右 · 素底结构图，几何取自提交 GeoJSON';
const LU_ZH_FOOT = '素底概念结构图 · 几何依据：land_use.geojson + roads.geojson + key_areas.geojson（EPSG:4326 投影示意）· 临时边界与概念中心线不得作为工程或审批依据。';
const SI_ZH_CAP = '素底概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位';
const SI_ZH_FOOT = '素底概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于修订、验证或替代任何规划边界';

const LU_EN_NOTE = 'Sheet rotated 90° · north to the right · plain-ground structure from the submitted GeoJSON';
const LU_EN_FOOT = 'Plain-ground concept structure · geometry: land_use / roads / key_areas.geojson (EPSG:4326, diagrammatic) · provisional lines are not engineering or approval data.';
const SI_EN_CAP = 'Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON';
const SI_EN_FOOT = 'Plain-ground concept structure from the submitted GeoJSON (EPSG:4326) · not for revising, validating or replacing any planning boundary';

module.exports = [
  {
    file: H + 'land-use-structure-zh.html',
    probes: ['.mapcap', '.mapcap .a', '.mapcap .b', '.ft', '.ftl'],
    candidates: [
      { name: 'A', edits: [
        ['.mapcap .b', '图面旋转 90° · 北向右 · OSM 路网底图上的概念结构图，几何取自提交 GeoJSON', LU_ZH_NOTE],
        ['.ftl', 'OSM 路网底图上的概念结构图 · 几何依据：land_use.geojson + roads.geojson + key_areas.geojson（EPSG:4326 投影示意）· 临时边界与概念中心线不得作为工程或审批依据。', LU_ZH_FOOT],
      ] },
    ],
  },
  {
    file: H + 'site-overview-zh.html',
    probes: ['.mapcap', '.mapcap .a', '.mapcap .b', '.ft', '.ft span:nth-child(1)'],
    candidates: [
      { name: 'A', edits: [
        ['.mapcap .b', 'OSM 路网底图上的概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位', SI_ZH_CAP],
        ['.ft span:nth-child(1)', 'OSM 路网底图上的概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于修订、验证或替代任何规划边界', SI_ZH_FOOT],
      ] },
    ],
  },
  {
    file: H + 'land-use-structure-en.html',
    probes: ['.mapcap', '.mapcap .a', '.mapcap .b', '.ft', '.ftl'],
    candidates: [
      { name: 'A-long', edits: [
        ['.mapcap .b', 'Sheet rotated 90° · north to the right · concept structure on an OSM road-network basemap, geometry from the submitted GeoJSON', LU_EN_NOTE],
        ['.ftl', 'Concept structure diagram on an OSM road-network basemap · geometry: land_use / roads / key_areas.geojson (EPSG:4326, diagrammatic) · provisional lines are not engineering or approval data.', LU_EN_FOOT],
      ] },
      { name: 'B-short', edits: [
        ['.mapcap .b', 'Sheet rotated 90° · north to the right · concept structure on an OSM road-network basemap', LU_EN_NOTE],
        ['.ftl', 'Concept structure on an OSM road-network basemap · geometry: land_use / roads / key_areas.geojson (EPSG:4326, diagrammatic) · provisional lines are not engineering or approval data.', LU_EN_FOOT],
      ] },
    ],
  },
  {
    file: H + 'site-overview-en.html',
    probes: ['.mapcap', '.mapcap .a', '.mapcap .b', '.ft', '.ft span:nth-child(1)'],
    candidates: [
      { name: 'A-long', edits: [
        ['.mapcap .b', 'Concept structure diagram on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON', SI_EN_CAP],
        ['.ft span:nth-child(1)', 'Concept structure diagram on an OSM road-network basemap, geometry from the submitted GeoJSON (EPSG:4326) · not for revising, validating or replacing any planning boundary', SI_EN_FOOT],
      ] },
      { name: 'B-short', edits: [
        ['.mapcap .b', 'Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON', SI_EN_CAP],
        ['.ft span:nth-child(1)', 'Concept structure on an OSM road-network basemap, from the submitted GeoJSON (EPSG:4326) · not for revising, validating or replacing any planning boundary', SI_EN_FOOT],
      ] },
    ],
  },
];
