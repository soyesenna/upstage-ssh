import { cli, define } from "gunshi";
import add from "./commands/add.js";

const subCommands = new Map();
subCommands.set("add", add);

const mainCommand = define({
  name: "upstage-ssh",
  description: "Manage ssh settings automatically",
  run: () => {
    console.log("upstage-ssh");
  },
});

cli(process.argv.slice(2), mainCommand, {
  name: "upstage-ssh",
  version: "0.0.1",
  description: "Manage ssh settings automatically",
  subCommands,
});
