// Presentation geometry only. Verification and growth calculations remain server-owned.
export function chartModel(row) {
 if(!row?.current||!row?.base||row.result?.status!=='verified'||!Array.isArray(row.result.issues)||row.result.issues.length||row.result.growth_pct==null)return null;
 const {current:a,base:b}=row;
 if(a.currency!==b.currency||a.currency==='USD'||a.scale!==b.scale||a.scope!==b.scope)return null;
 const bars=[{side:'current',fact:a},{side:'base',fact:b}].map(x=>({...x,value:Number(x.fact.value)}));
 if(bars.some(x=>x.fact.value==null||String(x.fact.value).trim()===''||!Number.isFinite(x.value)))return null;
 bars.sort((x,y)=>x.fact.start.localeCompare(y.fact.start)||x.fact.end.localeCompare(y.fact.end));
 const low=Math.min(0,...bars.map(x=>x.value)),high=Math.max(0,...bars.map(x=>x.value));
 const span=high-low||1,step=10**Math.floor(Math.log10(span));
 const min=low<0?Math.floor((low-span*.08)/step)*step:0,max=high>0?Math.ceil((high+span*.12)/step)*step:0;
 return {bars,min,max:max===min?min+1:max};
}
