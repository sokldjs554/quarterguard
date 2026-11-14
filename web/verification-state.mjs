// Retention is presentation only; a pending result must never be exported.
export function canRetainTable(live, previous, next) {
 if (!live || previous?.workflow_success !== true || !previous.rows?.length || !previous.selection) return false;
 return previous.selection.mode === next.mode && ['current','base'].every(side =>
  ['document','year','scope','period','currency'].every(key => previous.selection[side]?.[key] === next[side]?.[key]));
}
