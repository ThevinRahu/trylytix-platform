import { Outlet } from "react-router-dom";


const RootLayout = () => {
  return (
    // <Authenticator components={components}>
      // {() => (
        <main>
          <Outlet />
        </main>
      // )}
    // </Authenticator>
  );
};

export default RootLayout;
