select ir.serialised -> 'condition' -> 'when_all' -> 0 -> 'when' ->> 'value' as "conditions"
from ingestion_rule ir
join ingestion_ingestiontype ii on text(ii.id) = (ir.serialised ->> 'ingestion_type')
where ii."name" in ('Farm Products Used (Gatekeeper)')