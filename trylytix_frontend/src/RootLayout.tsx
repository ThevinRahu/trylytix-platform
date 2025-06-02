import { Authenticator } from "@aws-amplify/ui-react";
import { Outlet } from "react-router-dom";
import { AuthEventData } from "@aws-amplify/ui";

const components = {
  Header() {
    return (
      <div className="mt-36 mb-16 text-center w-[100%]">
        <h1 className="text-3xl font-semibold text-gray-700">
          TryLyTix
        </h1>
      </div>
    );
  },
};

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
