## Gemini models
### Gemini 2.5 Flash
Best model in terms of price-performance, offering well-rounded capabilities. 2.5 Flash is best for large scale processing, low-latency, high volume tasks that require thinking, and agentic use cases.
| Property           | Description                                   |
| :----------------- | :-------------------------------------------- |
| Model code         | models/gemini-2.5-flash           |
| **Token limits**   | **Input token limit:** 1,048,576                      | 
|                    | **Output token limit:** 65,536                    |
### Gemini 2.5 Flash Preview Text-to-Speech
Gemini 2.5 Flash Preview TTS is price-performant text-to-speech model, delivering high control and transparency for structured workflows like podcast generation, audiobooks, customer support, and more. Gemini 2.5 Flash rate limits are more restricted since it is an experimental / preview model.
| Property           | Description                                   |
| :----------------- | :-------------------------------------------- |
| Model code         | models/gemini-2.5-flash-preview-tts           |
| **Token limits**   | **Input token limit:** 8,000                      | 
|                    | **Output token limit:** 16,000                    |


## Usage tiers
Rate limits are tied to the project's usage tier. As your API usage and spending increase, you'll have an option to upgrade to a higher tier with increased rate limits.

The qualifications for Tiers 2 and 3 are based on the total cumulative spending on Google Cloud services (including, but not limited to, the Gemini API) for the billing account linked to your project.

### Free Tier
| Model |	RPM |	TPM |	RPD |
| :- | :- | :- | :- |
| Gemini 2.5 Flash |	10 |	250,000 |	250 |
| Gemini 2.5 Flash Preview TTS |	3 |	10,000 |	15 |
| Gemini 2.5 Pro Preview TTS  | 	|  | |

### Tier 1
| Model |	RPM |	TPM |	RPD | Batch Enqueued Tokens |
| :- | :- | :- | :- | :- |
| Gemini 2.5 Flash |	1,000 |	1,000,000 |	10,000 | 3,000,000| 
| Gemini 2.5 Flash Preview TTS    | 10	| 10,000 |	100 |
| Gemini 2.5 Pro Preview TTS  | 10	| 10,000 |	50 |