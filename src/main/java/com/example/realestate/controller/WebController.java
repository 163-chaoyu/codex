package com.example.realestate.controller;

import com.example.realestate.service.PriceDataService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {
    private final PriceDataService priceDataService;

    public WebController(PriceDataService priceDataService) {
        this.priceDataService = priceDataService;
    }

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("prices", priceDataService.getPrices());
        return "index";
    }
}
