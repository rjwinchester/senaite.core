import React from "react"
import ReactDOM from "react-dom"
import ReferenceField from "./components/ReferenceField.js"
import ReferenceResults from "./components/ReferenceResults.js"
import ReferenceWidgetAPI from "./api.js"


class ReferenceWidgetController extends React.Component {

  constructor(props) {
    super(props);

    let el = props.root_el;
    let api_url = el.dataset.api_url;
    let catalog_name = el.dataset.catalog_name;
    let base_query = el.dataset.base_query;
    let search_query = el.dataset.search_query;
    let columns = el.dataset.columns;
    let limit = el.dataset.limit || 10;

    // Internal state
    this.state = {
      id: el.dataset.id,
      name: el.dataset.name,
      // disabled flag for the field
      disabled: false,
      // query state
      catalog_name: catalog_name,
      base_query: this.parse_json(base_query),
      search_query: this.parse_json(search_query),
      columns: this.parse_json(columns),
      // the selected UIDs of the field
      selected: [],
      // records
      records: {},
      // the search query results
      results: [],
      // loading state
      loading: false,
      // multi valued
      multi: false,
      // limit results
      limit: limit
    }

    // Prepare API
    this.api = new ReferenceWidgetAPI({
      api_url: api_url,
    });

    // bind methods
    this.search = this.search.bind(this);
    this.search_all = this.search_all.bind(this);
    this.clear_results = this.clear_results.bind(this);
    this.select = this.select.bind(this);
    this.on_esc = this.on_esc.bind(this);

    return this
  }

  componentDidMount(){
    document.addEventListener("keydown", this.on_esc, false);
  }

  componentWillUnmount(){
    document.removeEventListener("keydown", this.on_esc, false);
  }

  parse_json(value) {
    /*
     * JSON parse the given value
     */
    if (value == null) {
      return null;
    }
    return JSON.parse(value)
  }

  getRequestOptions() {
    /*
     * HTTP POST options for the search server request
     */
    let options = {
      catalog_name: this.state.catalog_name,
      base_query: this.state.base_query,
      search_query: this.state.search_query,
      columns: this.state.columns
    }
    return options
  }

  select(uid, toggle) {
    console.debug("ReferenceWidgetController::select:uid:", uid);
    if (toggle == null) {
      toggle = true;
    }
    // create a copy of the selected UIDs
    let selected = [].concat(this.state.selected);
    if (toggle) {
      if (selected.indexOf(uid) == -1) {
        selected.push(uid);
      }
    } else {
      let pos = selected.indexOf(uid);
      if (pos > -1) {
        selected.splice(pos, 1);
      }
    }
    this.setState({selected: selected});
  }

  search(value) {
    /*
     * Call server ajax endpoint with the filter
     * TODO: debounce method!
     */
    console.debug("ReferenceWidgetController::search:value:", value);

    if (!value) {
      this.search_all();
      return null;
    }

    // remember the search value in the state
    let query = {Title: value + "*"}
    this.setState({search_query: query})

    // prepare the server request
    let self = this;
    this.toggle_loading(true);
    let options = this.getRequestOptions();
    let promise = this.api.search(options);
    promise.then(function(data) {
      console.debug("GOT REFWIDGET FILTER RESULTS: ", data);
      self.setState({results: data})
      self.toggle_loading(false);
    });
  }

  search_all() {
    /*
     * Search all results
     */
    // prepare the server request
    let self = this;
    this.toggle_loading(true);
    this.state.search_query = {};
    let options = this.getRequestOptions();
    let promise = this.api.search(options);
    promise.then(function(data) {
      console.debug("GOT REFWIDGET FILTER RESULTS: ", data);
      self.setState({results: data})
      self.toggle_loading(false);
    });
  }

  clear_results() {
    /*
     * Clear all search results
     */
    this.setState({results: []})
  }

  toggle_loading(toggle) {
    /*
     * Toggle loading state
     */
    if (toggle == null) {
      toggle = false;
    }
    this.setState({
      loading: toggle
    });
    return toggle;
  }

  on_esc(event){
    // Clear results on ESC key
    if(event.keyCode === 27) {
      this.clear_results();
    }
  }

  render() {
    return (
        <div className="referencewidget">
          <ReferenceField
            className="form-control"
            name={this.state.name}
            disabled={this.state.disabled}
            selected={this.state.selected}
            multi={this.state.multi}
            on_search={this.search}
            on_focus={this.search_all}
          />
          <ReferenceResults
            className="position-absolute shadow border rounded bg-white mt-1"
            columns={this.state.columns}
            selected={this.state.selected}
            results={this.state.results}
            limit={this.state.limit}
            on_select={this.select}
          />
        </div>
    );
  }
}

export default ReferenceWidgetController;
