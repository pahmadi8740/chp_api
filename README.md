# Connections Hypothesis Provider API Documentation
This README serves as the first iteration of the CHP API documentation. We may host a readthedocs at a later time but for now this will be the place to find all CHP endpoint documentation. We are also developing a lightweight python client that wraps the CHP endpoint into an easy to use python module. Please see [this documentation](https://github.com/di2ag/chp_client) for how to install and run the client and more information about our providers query semantics.

Our API is in active developement and are currently following [Translator Reasoner API standards](https://github.com/NCATSTranslator/ReasonerAPI) to the best of our ability as those standards are a moving target. 

Our API is currently live at: [chp.thayer.dartmouth.edu](http://chp.thayer.dartmouth.edu/)

## Open Endpoints
* [query](query.md) : `POST /query/`
* [predicates](predicates.md) : `GET /predicates/`
* [curies](curies.md) : `GET /curies/`
