select p1.pat_id
    ,p2.pat_name
    ,case when p2.home_phone like '000%' then '' else p2.home_phone end 
        || ' ' || 
            case when cts.cell_phone  like '000%' then '' else cts.cell_phone end phone_nums
    ,p2.add_line_1 || ' ' || p2.add_line_2 address
    ,p2.city
    ,p1.state
    ,p1.zip
from i2b2.lz_clarity_patient p1
join patient p2 on p1.pat_id = p2.pat_id
join i2b2.lz_clarity_pat_contacts cts on cts.pat_id = p1.pat_id
where p1.birth_date = to_date(:1,'yyyy-mm-dd')
    and p1.sex = :2