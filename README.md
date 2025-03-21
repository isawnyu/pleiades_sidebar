# Pleiades Sidebar

This code supports a planned portlet on Pleiades gazetteer place pages to replace the old Peripleo/Pelagios portlet. The new portlet will summarize and link to information resources outside Pleiades that are managed by partner projects and institutions and that, via metadata sharing, assert relationships to corresponding Pleiades places. This code outputs JSON files for each Pleiades place references by at least one other project containing summary information (URI, label, summary, representative point, other links) about each external information object. These JSON files are grouped by external partner or dataset and the individual entries conform to Linked Places Format (for other gazetteers) or Linked Traces Format (for artifacts and the like).

The data can be found in the [pleiades.datasets](https://github.com/isawnyu/pleiades.datasets) package here: https://github.com/isawnyu/pleiades.datasets/tree/main/data/sidebar.

## Supported external resources (roadmap)

- [ ] [Ancient Ports - Ports Antiques](https://www.ancientportsantiques.com/)
- [ ] [Archaeocosmos](http://archaeocosmos.arch.uoa.gr/)
- [x] [Chronique des fouilles en ligne/Archaeology in Greece Online](https://chronique.efa.gr)
- [ ] [Digital Periegesis](https://www.periegesis.org/en/)
- [x] [Epigraphic Database Heidelberg Geographic Database](https://edh.ub.uni-heidelberg.de/geographie/suche)
- [ ] [Gazetteer of Ancient Arabia](https://ancientarabia.huma-num.fr/gazetteer)
- [ ] [iDAI gazetteer (German Archaeological Institute)](https://gazetteer.dainst.org/)
- [ ] [Inscriptions of Sicily](http://sicily.classics.ox.ac.uk/)
- [x] [Itiner-e](https://itiner-e.org/)
- [x] [MANTO](https://www.manto-myth.org/manto)
- [x] [Nomisma](https://nomisma.org/)
- [ ] [PAThs Atlas](https://atlas.paths-erc.eu/map/saved/all_ms_places) - data is readily available on line in bulk
- [ ] [Syriac gazetteer](https://syriaca.org/geo/index.html)
- [ ] [Temples of the Classical World](https://romeresearchgroup.org/database-of-temples/) - data is readily available on line in bulk
- [ ] [ToposText](https://topostext.org/) - data is readily available on line in bulk, but out of date
- [ ] [Trismegistos Geo](https://www.trismegistos.org/geo/)
- [ ] [Vici.org](https://vici.org)
- [x] Wikidata, [via a TSV dump of a SPARQL query](https://github.com/isawnyu/pleiades_wikidata/)
- [ ] [World Historical Gazetteer](https://whgazetteer.org/)
- ??? (email pleiades.admin@nyu.edu to discuss adding your online open resource here)
