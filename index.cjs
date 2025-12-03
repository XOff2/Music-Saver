const { 
    Client, 
    GatewayIntentBits,
    Partials,
    EmbedBuilder,
    ActionRowBuilder,
    ButtonBuilder,
    ButtonStyle
} = require("discord.js");

const TOKEN = process.env.TOKEN;

// Your saved music commands
const musicList = [
    { name: "Shape of You", command: "/play shape of you" },
    { name: "Believer", command: "/play believer" },
    { name: "Faded", command: "/play faded" }
];

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ],
    partials: [Partials.Channel]
});

// Prefix command (no slash)
const PREFIX = "m"; // Example: "m" → user types: m

client.on("messageCreate", async (msg) => {
    if (msg.author.bot) return;

    if (msg.content.toLowerCase() === PREFIX) {
        
        const embed = new EmbedBuilder()
            .setColor("#5865F2")
            .setTitle("🎵 Music Selector")
            .setDescription("Choose a track and I will prepare the command for you.")
            .setFooter({ text: "Made for your server ❤️" });

        const rows = [];

        // Each row can hold up to 5 buttons
        for (let i = 0; i < musicList.length; i += 5) {
            const row = new ActionRowBuilder();
            const slice = musicList.slice(i, i + 5);

            slice.forEach(item => {
                row.addComponents(
                    new ButtonBuilder()
                        .setCustomId(`music_${item.name}`)
                        .setLabel(item.name)
                        .setStyle(ButtonStyle.Primary)
                );
            });

            rows.push(row);
        }

        msg.channel.send({
            embeds: [embed],
            components: rows
        });
    }
});

// When user clicks a button
client.on("interactionCreate", async (interaction) => {
    if (!interaction.isButton()) return;

    const id = interaction.customId;

    if (id.startsWith("music_")) {
        const songName = id.replace("music_", "");
        const song = musicList.find(x => x.name === songName);

        if (!song) return interaction.reply({ content: "Error: Not found.", ephemeral: true });

        // "prefill" message (works like suggestion)
        return interaction.reply({
            content: `\`\`\`\n${song.command}\n\`\`\`\nClick to copy the command above, then send it yourself.`,
            ephemeral: true
        });
    }
});

client.login(TOKEN);
