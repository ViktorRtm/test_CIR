def postprocessing(addresses_data:dict, period:int, date:str) -> dict[list[int]]:
    """
    Summarizes data according to a specified period
    
    :param addresses_data: Data of cameras with detection results
    :type addresses_data: dict
    :param period: Еhe period for which it is necessary to sum up. In minutes.
    :type period: int
    :param date: date when record video
    :type date: str
    :return: summarized data for each chamber over the period
    :rtype: dict[list[int], Any]
    """
    

    first_idx = 0
    second_idx = first_idx + period

    period_results = {key:[] for key in addresses_data}
    addresses = [key for key in addresses_data]
    data_lenght = len(addresses_data[addresses[0]]['results'][date])

    if data_lenght < second_idx:
        second_idx = data_lenght

    while second_idx < data_lenght:
        for key in addresses:
            period_sum = sum(addresses_data[key]['results'][date][first_idx:second_idx])
            period_results[key].append(period_sum)
        first_idx += period
        second_idx += period

    
    return period_results
