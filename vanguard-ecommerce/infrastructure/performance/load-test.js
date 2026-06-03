import http from "k6/http";
import { sleep } from "k6";

export const options = {
  vus: 500,
  duration: "1m"
};

export default function () {
  http.get(__ENV.BASE_URL ?? "http://localhost:3000");
  sleep(1);
}
