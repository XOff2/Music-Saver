import {
  Client,
  GatewayIntentBits,
  EmbedBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  Events
} from "discord.js";
import dotenv from "dotenv";
dotenv.config();

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Your internal music list
const musicList = [
  { name: "Shape of You", cmd: "/play shape of you" },
  { name: "Believer", cmd: "/play believer" },
  { name: "Faded", cmd: "/play faded" },
  { name: "Animals", cmd: "/play animals" }
];

// Handle slash commands
client.on(Events.InteractionCreate, async interaction => {
  if (!interaction.isChatInputCommand()) return;

  // /help command
  if (interaction.commandName === "help") {
    const embed = new EmbedBuilder()
      .setColor("#5865F2")
      .setTitle("🎵 Bot Command List")
      .setDescription("Here are the available commands:")
      .addFields(
        { name: "/search {name}", value: "Search music" },
        { name: "/help", value: "Show this menu" }
      );

    return interaction.reply({ embeds: [embed], ephemeral: true });
  }

  // /search command
  if (interaction.commandName === "search") {
    const query = interaction.options.getString("name").toLowerCase();
    const results = musicList.filter(m => m.name.toLowerCase().includes(query));

    if (results.length === 0) {
      return interaction.reply({
        content: "No track found.",
        ephemeral: true
      });
    }

    const track = results[0];

    const embed = new EmbedBuilder()
      .setColor("#ffb347")
      .setTitle("🎶 Music Found")
      .addFields({
        name: "Track",
        value: `**${track.name}**`
      });

    const btn = new ButtonBuilder()
      .setCustomId(`sendcmd_${track.cmd}`)
      .setLabel("Send to me")
      .setStyle(ButtonStyle.Primary)
      .setEmoji("📩");

    const row = new ActionRowBuilder().addComponents(btn);

    return interaction.reply({
      embeds: [embed],
      components: [row],
      ephemeral: true
    });
  }
});

// Handle button click
client.on(Events.InteractionCreate, async interaction => {
  if (!interaction.isButton()) return;

  if (interaction.customId.startsWith("sendcmd_")) {
    const cmd = interaction.customId.replace("sendcmd_", "");

    await interaction.user.send(
      `Here is your command:\n\`${cmd}\``
    );

    return interaction.reply({
      content: "Sent to your DM!",
      ephemeral: true
    });
  }
});

client.login(process.env.TOKEN);
