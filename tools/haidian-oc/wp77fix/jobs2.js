const A=require('path').resolve(__dirname, '../', 'w81-basemap/html') + "/";
const B=require('path').resolve(__dirname, '../', 'wp77fix/test-html') + "/";
const mk=(d,f,p)=>({file:d+f,probes:p});
const LU=['.mapcap','.mapcap .a','.mapcap .b','.ft','.ftl','.ftw'];
const SI=['.mapcap','.mapcap .a','.mapcap .b','.ft','.ft span:nth-child(1)','.ft span:nth-child(2)'];
module.exports=[
 mk(A,'land-use-structure-zh.html',LU), mk(B,'land-use-structure-zh.html',LU),
 mk(A,'land-use-structure-en.html',LU), mk(B,'land-use-structure-en.html',LU),
 mk(A,'site-overview-zh.html',SI),      mk(B,'site-overview-zh.html',SI),
 mk(A,'site-overview-en.html',SI),      mk(B,'site-overview-en.html',SI),
];
