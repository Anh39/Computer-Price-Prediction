import re
def extract_ram(input_str : str):
    input_str = input_str.upper()
    possible = [
        '4','8','12','16','20','24','32','48','64','128'
    ]
    for i in range(len(possible)-1,-1,-1):
        num = possible[i]
        ram_match = re.search(r'\b{}\s*GB\b'.format(num),input_str,re.IGNORECASE)
        if ram_match:
            ram_result = ram_match.group()
            if ('Tối đa lên tới {}'.format(ram_result).upper() not in input_str
                and 'Up to {}'.format(ram_result).upper() not in input_str):
                return ram_result
        else:
            continue
    return None

def extract_ddr(input_str : str):
    input_str = input_str.upper()
    possible = [
        '2','3','4','5','6'
    ]
    for i in range(len(possible)-1,-1,-1):
        num = possible[i]
        ram_match = re.search(r'\bDDR{}\b'.format(num),input_str,re.IGNORECASE)
        if ram_match:
            ram_result = ram_match.group()
            if ('Tối đa lên tới {}'.format(ram_result).upper() not in input_str
                and 'Up to {}'.format(ram_result).upper() not in input_str):
                return ram_result
        else:
            continue
    return None
print(extract_ddr("Ram: 8GB \nChipset Intel H470 ['BỘ NHỚ RAM']Dung lượng RAM 8GBLoại RAM DDR4T"))