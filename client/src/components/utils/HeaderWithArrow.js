import React from 'react';
import { ImArrowLeft2 } from 'react-icons/im';


const Header = ({ title, leftIconAction }) => {
  return (
    <div className='header-with-back-arrow'>
      <ImArrowLeft2  onClick={leftIconAction} size={30}/>
      <p>{title}</p>
    </div>
  );
};

export default Header;
