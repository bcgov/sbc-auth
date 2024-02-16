-- Admins contacts of BCA accounts who purchased invoices in the month of December 2022
select
	ps.org_id as "ACCOUNT NUMBER",
	o.type_code as "ACCOUNT TYPE",
	o.access_type as "ACCESS TYPE",
	o.status_code as "ACCOUNT STATUS",
	o.name as "ACCOUNT NAME",
	o.branch_name as "BRANCH NAME",
	m.membership_type_code as "USER TYPE",
	o.bcol_user_id as "BCOL USER ID",
	u.first_name || ' ' ||u.last_name as "USER NAME",
	u.email as "USER EMAIL",
	(case when u.status = 1 then 'ACTIVE' else 'INACTIVE' end) as "USER STATUS",
	c.street as "ADDRESS 1",
	c.street_additional as "ADDRESS 2",
	c.city as "CITY",
	c.region as "PROVINCE",
	c.country as "COUNTRY",
	c.postal_code as "POSTAL CODE",
	c2.email as "FIRST ADMIN EMAIL",
	c2.phone as "FIRST ADMIN PHONE"
from
orgs o
INNER JOIN product_subscriptions ps ON o.id = ps.org_id
INNER JOIN memberships m ON o.id = m.org_id
INNER JOIN contact_links cl ON cl.org_id = o.id --the contact info which pertains to the admin’s of an ORG
INNER JOIN users u on u.id = m.user_id
INNER JOIN contacts c on c.id = cl.contact_id
LEFT JOIN contact_links cl2 on cl2.user_id = m.user_id
LEFT JOIN contacts c2 on c2.id = cl2.contact_id 

where 
ps.product_code = 'BCA' 
and membership_type_code = 'ADMIN'
-- and o.id in ('') -- GRAB FROM PAY query. "--This line removed, cause it has syntax error if not specify ids--"

order by 3 desc;
