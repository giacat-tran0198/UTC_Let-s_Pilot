import { combineReducers } from 'redux';
import userReducer from './user.reducer';
import chatReducer from './chat.reducer';

export default combineReducers({
  userReducer,
  chatReducer,
});
