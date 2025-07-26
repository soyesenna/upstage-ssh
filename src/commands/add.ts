import { define } from "gunshi";

const add = define({
  name: "add",
  description: "Add a new ssh settings, like host, username, port, etc.",
  args: {
    host: {
      type: "string",
      description: "The host of the ssh settings",
      short: "o",
    },
    username: {
      type: "string",
      description: "The user of the ssh settings",
      short: "u",
    },
    port: {
      type: "number",
      description: "The port of the ssh settings",
      default: 22,
      short: "p",
    },
    key: {
      type: "string",
      description: "The key of the ssh settings",
      short: "k",
    },
  },
  run: (ctx) => {
    console.log(ctx.values);
  },
});

export default add;