const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// Local music list
const musicList = [
    { name: "Shape of You", command: "/play Shape of You" },
    { name: "Faded", command: "/play Faded" },
    { name: "Unholy", command: "/play Unholy" },
    { name: "Blinding Lights", command: "/play Blinding Lights" },
];

client.on("messageCreate", async (message) => {
    if (message.author.bot) return;

    // Main command
    if (message.content.startsWith("!search")) {
        const query = message.content.replace("!search", "").trim();
        if (!query) {
            return message.reply("❗ **Please type a music name.**");
        }

        const results = musicList.filter(m =>
            m.name.toLowerCase().includes(query.toLowerCase())
        );

        if (results.length === 0) {
            return message.reply("🔍 **No results found.**");
        }

        for (const song of results) {
            const embed = new EmbedBuilder()
                .setColor("#5865F2")
                .setTitle(`🎵 Found: **${song.name}**`)
                .setDescription("Click the button below to load the command.")
                .setFooter({ text: "Music Search Bot" });

            const row = new ActionRowBuilder().addComponents(
                new ButtonBuilder()
                    .setLabel("Load Command")
                    .setCustomId(`load_${song.command}`)
                    .setStyle(ButtonStyle.Primary)
            );

            await message.channel.send({
                embeds: [embed],
                components: [row]
            });
        }
    }
});

client.on("interactionCreate", async (interaction) => {
    if (!interaction.isButton()) return;

    const cmd = interaction.customId.replace("load_", "");

    try {
        await interaction.reply({
            content: `💬 Your command is ready:\n\`${cmd}\`\n\nJust press **Enter** to send it.`,
            ephemeral: true
        });

        await interaction.user.send(`💬 Auto-filled command:\n\`${cmd}\``)
            .catch(() => {});

    } catch (err) {
        console.error(err);
    }
});

client.login(process.env.TOKEN);
