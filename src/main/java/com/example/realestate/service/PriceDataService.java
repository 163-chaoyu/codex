package com.example.realestate.service;

import com.example.realestate.model.CommunityPrice;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

@Service
public class PriceDataService {
    private final ObjectMapper objectMapper;
    private final String dataFile;

    public PriceDataService(ObjectMapper objectMapper,
                            @Value("${app.data.file:data/nanjing_prices.json}") String dataFile) {
        this.objectMapper = objectMapper;
        this.dataFile = dataFile;
    }

    public List<CommunityPrice> getPrices() {
        List<CommunityPrice> prices = readFromFileSystem();
        if (prices.isEmpty()) {
            prices = readFromClasspath();
        }

        prices.sort(Comparator.comparingInt(CommunityPrice::getAvgUnitPrice).reversed());
        return prices;
    }

    private List<CommunityPrice> readFromFileSystem() {
        Path path = Path.of(dataFile);
        if (!Files.exists(path)) {
            return Collections.emptyList();
        }

        try (InputStream inputStream = Files.newInputStream(path)) {
            return objectMapper.readValue(inputStream, new TypeReference<>() {});
        } catch (IOException ex) {
            return Collections.emptyList();
        }
    }

    private List<CommunityPrice> readFromClasspath() {
        ClassPathResource resource = new ClassPathResource("data/nanjing_prices.json");
        try (InputStream inputStream = resource.getInputStream()) {
            return objectMapper.readValue(inputStream, new TypeReference<>() {});
        } catch (IOException ex) {
            return Collections.emptyList();
        }
    }
}
