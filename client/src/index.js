import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './styles/index.scss';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import thunk from 'redux-thunk';
import axios from 'axios';
import rootReducer from './reducers';

let store;

if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development') {
  // dev code
  store = createStore(rootReducer, composeWithDevTools(applyMiddleware(thunk)));
} else {
  // production code
  store = createStore(rootReducer, applyMiddleware(thunk));
}

// Setting the base URL of the API
export const API_URL =
  window.location.protocol === 'https:'
    ? `https://${window.location.hostname}:5000`
    : `http://${window.location.hostname}:5000`;

// Telling axios what is the baseURL to use for the requests
axios.defaults.baseURL = API_URL;

ReactDOM.render(
  <Provider store={store}>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </Provider>,
  document.getElementById('root')
);
