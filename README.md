# Web Application for Visualizing 2022 U.S. House Election Results

<img width="1438" alt="Screenshot 2023-12-22 at 10 58 03 AM" src="https://github.com/wongella123/USElectionAnalysis/assets/121847745/6b12e0d6-2846-42cf-aacf-87fdfb540d5a">

# Code Description
The code is divided into two major parts.

1st: Using BeautifulSoup and Selenium to do web scraping for extracting the US 2022 Election results

2nd: Using Dash, a Python framework for building analytical web applications, visualizing the 2022 U.S. House Election results with various components such as choropleth maps, bar charts, scatter plots, 3D plots, and a treemap to represent different aspects of the election results.

# Detail Explanation

I developed a web application using Python and the Dash framework to visualize the results of the 2022 U.S. House Elections. The application incorporates various interactive visualizations, enabling users to explore and analyze the election data in an intuitive and informative manner.

The application includes a choropleth map that displays the election results for each district, allowing users to zoom in on specific states and obtain detailed information about winners, winning parties, and vote percentages. Users can also select a particular district to view a pie chart illustrating the distribution of votes among candidates within that district.

To provide a broader perspective, the application features bar charts showcasing the total votes received across all states, as well as votes received per state. The bar charts can be customized with different hover modes for enhanced data exploration.

In addition, the application presents a scatter plot and a 3D axes diagram to compare voter turnout with party affiliation, facilitating deeper analysis of the election dynamics. Users can also explore the party affiliation of incumbents in each district through a dedicated choropleth map, offering insights into the political landscape.

A slider feature allows users to toggle between Republican and Democratic parties, dynamically updating a bar chart to display the top ten percentages of votes received by incumbents from the selected party.

Moreover, the application utilizes a treemap to visually represent the election results, presenting the party, state, and candidate names, with rectangle sizes indicating vote counts and colors denoting vote percentages.

This web application provides an engaging and comprehensive platform for visualizing and understanding the 2022 U.S. House Election results. Its interactive features and informative visualizations empower users to gain valuable insights into the electoral landscape, making it an invaluable tool for researchers, political analysts, and anyone interested in exploring the election data in a user-friendly manner.
