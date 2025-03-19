from django.db.models import Q
from User.models import User

def get_receiver_ids(related_to, targeting_data):
    """
    Get a list of receiver user IDs based on the targeting type and provided data.
    
    Parameters:
        related_to (str): One of 'M', 'T', or 'D'
        targeting_data (dict): Data required for each type:
            - For 'M': {'user_ids': [list of user ids]}
            - For 'T': {'task_ids': [list of task ids]}
            - For 'D': {'criteria': { '2nd': ['backend', 'frontend'], '3rd': ['ui/ux'], ... }}
    
    Returns:
        list: Unique user IDs as a list.
    """

    if related_to == 'M':
        return targeting_data.get('user_ids', [])
    
    elif related_to == 'T':
        task_ids = targeting_data.get('task_ids', [])
        # Query users based on tasks assigned to groups.
        return list(
            User.objects.filter(
                group_members__task__id__in=task_ids
            ).values_list('id', flat=True).distinct()
        )
    
    elif related_to == 'D':
        criteria = targeting_data.get('criteria', {})
        query = Q()
        for year, domains in criteria.items():
            query |= Q(year=year, domain__in=domains)
        return list(
            User.objects.filter(query).values_list('id', flat=True).distinct()
        )
    
    else:
        return []