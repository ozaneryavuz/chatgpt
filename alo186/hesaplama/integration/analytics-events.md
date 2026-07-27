# Önerilen GA4 olayları

| Olay | Parametreler |
|---|---|
| `ups_calculation_completed` | `mode`, `load_w`, `solution_class` |
| `ups_preset_selected` | `preset_w` |
| `ev_calculation_completed` | `charger_kw`, `phase`, `charge_hours` |
| `voltage_drop_completed` | `system`, `material`, `drop_percent`, `section_mm2` |
| `outage_plan_generated` | `profile`, `duration`, `task_count` |
| `outage_plan_saved` | `profile` |

## Key event adayları

- `ups_calculation_completed`
- `ev_calculation_completed`
- `outage_plan_saved`
- profesyonel hizmet CTA tıklamaları

## Ortak parametre

Bütün olaylara `tool_location` otomatik eklenir.

## Yayın sonrası dashboard

Araç bazında şu funnel izlenmelidir:

`landing → form_started → calculation_completed → next_action_clicked → affiliate_or_service_conversion`
