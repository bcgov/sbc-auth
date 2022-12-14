---BCA USERS/ BCA ACCOUNTS:  Naming Convention should be BCA_USERS_ACCOUNTS_YYYYMMDD
---(example:BCA_USERS_ACCOUNTS_20221001)

select
	ps.org_id as "ACCOUNT NUMBER",
	o.type_code as "ACCOUNT TYPE",
	o.access_type as "ACCESS TYPE",
	o.status_code as "ACCOUNT STATUS",
	o.name as "ACCOUNT NAME",
	o.branch_name as "BRANCH NAME",
	m.membership_type_code as "USER TYPE",
	u.first_name || ' ' ||u.last_name as "USER NAME",
	u.email as "USER EMAIL", -- USER PROFILE	
	(case when u.status = 1 then 'ACTIVE' else 'INACTIVE' end) as "USER STATUS" -- if 1 ACTIVE | 2 INACTIVE
	c.street as "ADDRESS 1",
	c.street_additional as "ADDRESS 2",
	c.city as "CITY",
	c.region as "PROVINCE",
	c.country as "COUNTRY",
	c.postal_code as "POSTAL CODE",
	c.email as "FIRST ADMIN EMAIL", -- the contact info which pertains to the admin’s of an ORG
	c.phone as "FIRST ADMIN PHONE", --the contact info which pertains to the admin’s of an ORG


from
orgs o
INNER JOIN product_subscriptions ps ON o.id = ps.org_id
INNER JOIN memberships m ON o.id = m.org_id
INNER JOIN contact_links cl ON cl.org_id = o.id --the contact info which pertains to the admin’s of an ORG
INNER join users u on u.id = m.user_id
INNER join contacts c on c.id = cl.contact_id
where 
ps.product_code = 'BCA' 
and 
to_char(o.created ,'YYYY-MM') = '2022-09'---change to month you need data for

order by 3 desc;