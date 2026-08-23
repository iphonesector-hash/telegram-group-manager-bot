-- Keep order lifecycle values aligned with API order creation.
-- `registered` represents non-VPN services awaiting fulfilment and
-- `delivered` represents rewards that were delivered immediately.
alter table public.isectorbot_orders
  drop constraint if exists isectorbot_orders_status_check;

alter table public.isectorbot_orders
  add constraint isectorbot_orders_status_check
  check (status in (
    'pending',
    'registered',
    'active',
    'delivered',
    'expired',
    'cancelled'
  ));
