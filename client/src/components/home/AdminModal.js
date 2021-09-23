import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { archiveUser, demoteUser, promoteUser, unarchiveUser } from '../../actions/admin.action';

const AdminPage = ({ outsideClickAction }) => {
  const dispatch = useDispatch();
  const userStates = useSelector(state => state.userReducer)
  const [login, setLogin] = useState('');

  const handleArchiveUser = () => {
    dispatch(archiveUser(login))
  }
  const handleUnarchiveUser = () => {
    dispatch(unarchiveUser(login))
  }
  const handlePromoteUser = () => {
    dispatch(promoteUser(login));
  }
  const handleDemoteUser = () => {
    dispatch(demoteUser(login));
  }

  return (
    <div className='context-menu-backdrop' onClick={outsideClickAction}>
      <div
        className='addbylogin-modal'
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <input
          type='text'
          placeholder='login'
          value={login}
          onChange={(e) => setLogin(e.target.value)}
        />
        <div className='addbylogin-button-container'>
          <button onClick={handlePromoteUser}>Promote user</button>
          <button onClick={handleDemoteUser}>Demote user</button>
        </div>
        <div className='addbylogin-button-container'>
          <button onClick={handleArchiveUser}>Archive user</button>
          <button onClick={handleUnarchiveUser}>
            Unarchive user
          </button>
        </div>
        <p className='addbylogin-infobox'>{userStates.adminError}</p>
      </div>
    </div>
  );
};

export default AdminPage;
