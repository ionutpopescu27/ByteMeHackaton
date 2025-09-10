import React from 'react';

const Header = () => {
  return (
    <header className="header">
      {/* No logo here anymore */}
      <div></div> {/* Empty div to keep space left-aligned */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span style={{ marginRight: '10px', fontSize: '14px', color: 'white' }}></span>
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: '#FF5640',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            fontWeight: 'bold',
            color: 'white',
          }}
        >
          R
        </div>
      </div>
    </header>
  );
};

export default Header;
