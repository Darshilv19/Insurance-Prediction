1\. Header \& Filters	

* Dashboard Title: Premium Value \& Risk Factor Analysis (Font: Segoe UI Bold, Color: Dark Grey)



Filter (Slicer): Policy Type

* Style: Tile (Horizontal buttons) at the top right.
* Color: Mint Green background for selected items.



2\. The 3 KPIs (The Big Numbers)



KPI 1: Total Premium Revenue

* Field: Sum of Premium Amount



KPI 2: Average Premium per Customer

* Field: Average of Premium Amount



KPI 3: Premium-to-Income Ratio

* Calculation: (Average Premium / Average Annual Income) \* 100
* Insight: Shows how much of a customer's income is spent on your insurance



3\. The 6 Graphs (The Visuals)



Graph Name				Type		Axis/Details		Color Logic

1\. Premium Amount by Age Group		Area Chart	X: Age			Y: Premium Amount

2\. Impact of Smoking on Premium		Clustered Bar	Y: Smoking Status	X: Avg Premium

3\. Health Score vs. Premium		Scatter Plot	X: Health Score		Y: Premium Amount

4\. Premium Distribution by Occupation	Donut Chart	Legend: Occupation	Values: Premium

5\. Claims History vs. Premium Cost	Column Chart	X: Previous Claims	Y: Avg Premium

6\. Premium Trend by Policy Start Year	Line Chart	X: Policy Start Year	Y: Total Premium



Visual Settings \& Color Hex Codes

To ensure it looks professional and follows your constraints, use these specific shades:



Mint Green: #A8E6CF (Use for "Positive" metrics or Primary bars)

Soft Blue: #AED9E0 (Use for trends and lines)

Light Grey: #F5F5F5 (Use for chart backgrounds and borders)

Text: #4F4F4F (Dark grey for readability)





Quick DAX Measures to Add

If you want your dashboard to be more "dynamic," create these two simple measures:



* Premium YOY Growth:

Premium Growth = DIVIDE(\[Total Premium] - CALCULATE(\[Total Premium], PREVIOUSYEAR('Date'\[Date])), CALCULATE(\[Total Premium], PREVIOUSYEAR('Date'\[Date])))



* Risk Weighted Premium:

Avg Premium by Health = AVERAGE('Table'\[Premium Amount]) / AVERAGE('Table'\[Health Score])

















