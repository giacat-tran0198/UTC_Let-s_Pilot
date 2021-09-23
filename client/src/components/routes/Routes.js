import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from 'react-router-dom';
import Home from '../pages/Home';
import Chat from '../pages/Chat';
import SignIn from '../pages/SignIn';
import SignUp from '../pages/SignUp';
import MyAccount from '../pages/MyAccount';
import ChangePassword from '../pages/ChangePassword';
import CreateMeeting from '../pages/CreateMeeting';
import JoinMeeting from '../pages/JoinMeeting';
import ForgotPassword from '../pages/ForgotPassword'

const Routes = () => {
  
  return (
    <Router>
      <Switch>
        <Route path='/' exact component={SignIn} />
        <Route path='/signup' exact component={SignUp} />
        <Route path='/signin/forgot-password' exact component={ForgotPassword}/>
        <Route path='/home' exact component={Home} />
        <Route path='/chat' exact component={Chat} />
        <Route path='/account' exact component={MyAccount} />
        <Route path='/meeting/create' exact component={CreateMeeting} />
        <Route path='/meeting/join' exact component={JoinMeeting} />
        <Route path='/account/password' exact component={ChangePassword} />
        <Redirect to='/home' />
      </Switch>
    </Router>
  );
};

export default Routes;
