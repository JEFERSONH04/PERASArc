export const sessionSetService = (key, value) => {
  localStorage.setItem(key, value);
};

export const sessionGetService = (key) => {
  return localStorage.getItem(key);
};
