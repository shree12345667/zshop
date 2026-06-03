import { NestFactory } from "@nestjs/core";
import { Module } from "@nestjs/common";

@Module({})
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors();
  await app.listen(process.env.PORT ?? 3001);
}

void bootstrap();
