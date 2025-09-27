import { API_AUTH } from "@/conf";

export const loginService = async (username, password) => {
  const url = API_AUTH + "/login/";

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username,
      password: password,
    }),
  });

  const data = await response.json();
  return data;
};

export const registerService = async (username, email, password) => {
  const url = API_AUTH + "/register/";

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username,
      password: password,
      email: email,
    }),
  });

  const data = await response.json();
  return data;
};


