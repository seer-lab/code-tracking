def check_parcel(tracking_id, weight_kg, destination):
    """
    Validate a parcel and assign a shipping tier.

    Args:
        tracking_id (str):  Non-empty parcel identifier.
        weight_kg (float):  Parcel weight in kg (must be > 0 and <= 30).
        destination (str):  'domestic' or 'international'.

    Returns:
        dict: {
            'tier':             'standard', 'express', or None,
            'delivery_days':    int or None,
            'status':           'ok' or 'error',
            'message':          str
        }
    """
    if not isinstance(tracking_id, str) or not tracking_id.strip():
        return {'tier': None, 'delivery_days': None,
                'status': 'error', 'message': 'Invalid tracking ID'}

    if weight_kg <= 0 or weight_kg > 30:
        return {'tier': None, 'delivery_days': None,
                'status': 'error', 'message': 'Weight out of range'}

    if destination not in ('domestic', 'international'):
        return {'tier': None, 'delivery_days': None,
                'status': 'error', 'message': 'Unknown destination type'}

    if weight_kg <= 2:
        tier = 'express'
    else:
        tier = 'standard'

    if destination == 'domestic':
        delivery_days = 2 if tier == 'express' else 5
    else:
        delivery_days = 7 if tier == 'express' else 14

    return {'tier': tier, 'delivery_days': delivery_days,
            'status': 'ok', 'message': 'Parcel accepted'}